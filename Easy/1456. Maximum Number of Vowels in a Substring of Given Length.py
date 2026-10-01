class Solution(object):
    def maxVowels(self, s, k):

        total = 0

        for i in range(k):
            if s[i] in "aeiou":
                total += 1

        max_vowel = total

        for i in range(k, len(s)):
            if s[i] in "aeiou":
                total += 1

            if s[i - k] in "aeiou":
                total -= 1

            if total > max_vowel:
                max_vowel = total

        return max_vowel




if __name__ == "__main__":
    sol = Solution()
    s = "abciiidef"
    k = 3
    print(sol.maxVowels(s, k))
