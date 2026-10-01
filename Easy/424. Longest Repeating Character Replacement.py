class Solution(object):
    def characterReplacement(self, s, k):
        left = 0
        max_len = 0
        current_str = {}

        for i in range(len(s)):

            char = s[i]
            if char in  current_str:
                current_str[char] += 1
            else:
                current_str[char] = 1

            # Leo you are dumb and you know the windows size already so you can just i - left + 1 instead of sum(current_str.values())
            while (sum(current_str.values()) - max(current_str.values())) > k:
                current_str[s[left]] -= 1
                left += 1

            if sum(current_str.values()) > max_len:
                max_len = sum(current_str.values())

        return max_len


if __name__ == '__main__':
    s = "BAAA"
    k = 0
    solution = Solution()
    result = solution.characterReplacement(s, k)
    print(result)