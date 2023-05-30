## How to use

1. Go to the proxy directory and build the gpt-proxy image.
   ```bash
   cd proxy
   docker image build -t gpt-proxy:latest .
   ```

2. Copy your agent's configuration file to config.yaml
   ```bash
   cp config.yaml.example config.yaml
   vim config.yaml
   ```

3. Start services with docker compose.
   ```bash
   # v2
   docker compose up -d
   # v1
   docker-compose up -d
   ```

4. Populate environment variables in the `.env` file
   ```bash
   cp example.env .env
   vim .env
   ```
5. Run main.py and enter your question.
   ```bash
   > pip install -r requirements.txt
   > python main.py --help
   Usage: main.py [OPTIONS] COMMAND [ARGS]...

   ─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────
   | --install-completion          Install completion for the current shell.                                         |
   | --show-completion             Show completion for the current shell, to copy it or customize the installation.  |
   | --help                        Show this message and exit.                                                       |
   ─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────
   | bard                                                                                                            |
   | chatgpt                                                                                                         |
   | translate                                                                                                       |
   ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   ```

## Examples

1. translate
   ```bash
   > python main.py translate
   > Source [zh]: en
   > Target [en]: zh
   ask for answer(press Enter twice to finish):
   > how old are you?
   你多大了？
   ```

2. chatgpt
   ```python
   > python main.py chatgpt
   > Plus [y/N]:
   Using ChatGPT...
   http://127.0.0.1:19090/api/
   ask for answer(press Enter twice to finish):
   > 如何使用 KMP 算法，请用 Python 为我详细举例解释，我很希望可以学会 KMP 算法

   当然！KMP（Knuth-Morris-Pratt）算法是一种用于在文本中快速查找子串的字符串匹配算法。它通过利用已经匹配的信息，避免在文本中重复比较已经比较过的字符。

   下面是使用 Python 实现 KMP 算法的示例代码：

   def compute_lps(pattern):
      """
      计算最长公共前缀和最长公共后缀的部分匹配表（Longest Proper Prefix/Suffix）
      """
      length = len(pattern)
      lps = [0] * length  # 初始化部分匹配表

      prefix_len = 0  # 当前最长公共前缀的长度
      i = 1

      while i < length:
         if pattern[i] == pattern[prefix_len]:
               prefix_len += 1
               lps[i] = prefix_len
               i += 1
         else:
               if prefix_len != 0:
                  prefix_len = lps[prefix_len - 1]
               else:
                  lps[i] = 0
                  i += 1

      return lps


   def kmp_search(text, pattern):
      """
      使用 KMP 算法在文本中查找模式串
      """
      n = len(text)
      m = len(pattern)
      result = []

      lps = compute_lps(pattern)
      i = 0  # text 中当前字符的索引
      j = 0  # pattern 中当前字符的索引

      while i < n:
         if text[i] == pattern[j]:
               i += 1
               j += 1

               if j == m:
                  result.append(i - j)  # 找到匹配，将索引添加到结果列表
                  j = lps[j - 1]
         else:
               if j != 0:
                  j = lps[j - 1]
               else:
                  i += 1

      return result


   # 示例用法
   text = "ABABDABACDABABCABAB"
   pattern = "ABABCABAB"
   result = kmp_search(text, pattern)
   print("在文本中的匹配位置：", result)

   ```

3. bard
   ```bash
   > python main.py bard
   Using Google Bard...
   ask for answer(press Enter twice to finish):
   > implement fib method via python

   Sure, here is the implementation of the Fibonacci sequence in Python:


   def fib(n):
      """
      Calculates the nth Fibonacci number.

      Args:
      n: The nth Fibonacci number to calculate.

      Returns:
      The nth Fibonacci number.
      """

      if n == 0 or n == 1:
          return n
      else:
          return fib(n - 1) + fib(n - 2)


   This function works by recursively calculating the Fibonacci numbers. The base cases are when n is 0 or 1, in which case the function simply returns n. Otherwise, the function returns the sum of the two previous Fibonacci numbers.

   Here is an example of how to use the function:


   >>> fib(10)
   55


   This code will print the 10th Fibonacci number, which is 55.

   The Fibonacci sequence is a famous mathematical sequence that has many interesting properties. It can be used to solve a variety of problems, including finding the golden ratio and calculating the number of ways to arrange a set of
   objects.
   ```

## Thanks

This demo reference [acheong08](https://github.com/acheong08)'s open source project, many thanks 🙏.