package main

import (
	"io"
	"log"
	"os"
	"strings"
	"time"

	http "github.com/bogdanfinn/fhttp"
	tls_client "github.com/bogdanfinn/tls-client"

	"github.com/acheong08/OpenAIAuth/auth"
	"github.com/acheong08/endless"
	"github.com/gin-gonic/gin"
)

type auth_struct struct {
	OpenAI_Email    string `json:"openai_email"`
	OpenAI_Password string `json:"openai_password"`
}

var (
	jar     = tls_client.NewCookieJar()
	options = []tls_client.HttpClientOption{
		tls_client.WithTimeoutSeconds(360),
		tls_client.WithClientProfile(tls_client.Safari_IOS_16_0),
		tls_client.WithNotFollowRedirects(),
		tls_client.WithCookieJar(jar), // create cookieJar instance and pass it as argument
	}
	client, _      = tls_client.NewHttpClient(tls_client.NewNoopLogger(), options...)
	user_agent     = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
	http_proxy     = os.Getenv("http_proxy")
	authorizations auth_struct
	OpenAI_HOST    = os.Getenv("OPENAI_HOST")
)

func admin(c *gin.Context) {
	if c.GetHeader("Authorization") != os.Getenv("PASSWORD") {
		c.String(401, "Unauthorized")
		c.Abort()
		return
	}
	c.Next()
}

func init() {
	if OpenAI_HOST == "" {
		OpenAI_HOST = "chat.openai.com"
	}
	authorizations.OpenAI_Email = os.Getenv("OPENAI_EMAIL")
	authorizations.OpenAI_Password = os.Getenv("OPENAI_PASSWORD")
	if authorizations.OpenAI_Email != "" && authorizations.OpenAI_Password != "" {
		go func() {
			for {
				authenticator := auth.NewAuthenticator(authorizations.OpenAI_Email, authorizations.OpenAI_Password, http_proxy)
				err := authenticator.Begin()
				if err != nil {
					log.Println(err)
					break
				}
				puid, err := authenticator.GetPUID()
				if err != nil {
					break
				}
				os.Setenv("PUID", puid)
				println(puid)
				time.Sleep(24 * time.Hour * 7)
			}
		}()
	}
}

func main() {

	if http_proxy != "" {
		client.SetProxy(http_proxy)
		println("Proxy set:" + http_proxy)
	}

	PORT := os.Getenv("PORT")
	if PORT == "" {
		PORT = "9090"
	}
	handler := gin.Default()
	handler.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "pong"})
	})

	handler.PATCH("/admin/puid", admin, func(c *gin.Context) {
		// Get the password from the request (json) and update the password
		type puid_struct struct {
			PUID string `json:"puid"`
		}
		var puid puid_struct
		err := c.BindJSON(&puid)
		if err != nil {
			c.String(400, "puid not provided")
			return
		}
		// Set environment variable
		os.Setenv("PUID", puid.PUID)
		c.String(200, "puid updated")
	})
	handler.PATCH("/admin/password", admin, func(c *gin.Context) {
		// Get the password from the request (json) and update the password
		type password_struct struct {
			PASSWORD string `json:"password"`
		}
		var password password_struct
		err := c.BindJSON(&password)
		if err != nil {
			c.String(400, "password not provided")
			return
		}
		// Set environment variable
		os.Setenv("PASSWORD", password.PASSWORD)
		c.String(200, "PASSWORD updated")
	})
	handler.PATCH("/admin/openai", admin, func(c *gin.Context) {
		err := c.BindJSON(&authorizations)
		if err != nil {
			c.JSON(400, gin.H{"error": "JSON invalid"})
		}
		os.Setenv("OPENAI_EMAIL", authorizations.OpenAI_Email)
		os.Setenv("OPENAI_PASSWORD", authorizations.OpenAI_Password)
	})

	handler.Any("/api/*path", proxy)

	gin.SetMode(gin.ReleaseMode)
	endless.ListenAndServe(os.Getenv("HOST")+":"+PORT, handler)
}

func proxy(c *gin.Context) {
	// Remove _cfuvid cookie from session
	jar.SetCookies(c.Request.URL, []*http.Cookie{})

	var url string
	var err error
	var request_method string
	var request *http.Request
	var response *http.Response

	if c.Request.URL.RawQuery != "" {
		url = "https://" + OpenAI_HOST + "/backend-api" + c.Param("path") + "?" + c.Request.URL.RawQuery
	} else {
		url = "https://" + OpenAI_HOST + "/backend-api" + c.Param("path")
	}
	request_method = c.Request.Method

	request, err = http.NewRequest(request_method, url, c.Request.Body)
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	request.Header.Set("Host", ""+OpenAI_HOST+"")
	request.Header.Set("Origin", "https://"+OpenAI_HOST+"/chat")
	request.Header.Set("Connection", "keep-alive")
	request.Header.Set("Content-Type", "application/json")
	request.Header.Set("Keep-Alive", "timeout=360")
	request.Header.Set("Authorization", c.Request.Header.Get("Authorization"))
	request.Header.Set("sec-ch-ua", "\"Chromium\";v=\"112\", \"Brave\";v=\"112\", \"Not:A-Brand\";v=\"99\"")
	request.Header.Set("sec-ch-ua-mobile", "?0")
	request.Header.Set("sec-ch-ua-platform", "\"Linux\"")
	request.Header.Set("sec-fetch-dest", "empty")
	request.Header.Set("sec-fetch-mode", "cors")
	request.Header.Set("sec-fetch-site", "same-origin")
	request.Header.Set("sec-gpc", "1")
	request.Header.Set("user-agent", user_agent)
	if os.Getenv("PUID") != "" {
		request.Header.Set("cookie", "_puid="+os.Getenv("PUID")+";")
	}
	puid_cookie, err := c.Request.Cookie("_puid")
	if err == nil {
		request.Header.Set("cookie", "_puid="+puid_cookie.Value+";")
	}

	response, err = client.Do(request)
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}
	defer response.Body.Close()
	// Copy headers from response
	for k, v := range response.Header {
		if strings.ToLower(k) == "content-encoding" {
			continue
		}
		c.Header(k, v[0])
	}
	// Get status code
	c.Status(response.StatusCode)

	buf := make([]byte, 4096)
	for {
		n, err := response.Body.Read(buf)
		if n > 0 {
			_, writeErr := c.Writer.Write(buf[:n])
			if writeErr != nil {
				log.Printf("Error writing to client: %v", writeErr)
				break
			}
			c.Writer.Flush() // flush buffer to make sure the data is sent to client in time.
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Printf("Error reading from response body: %v", err)
			break
		}
	}
}
