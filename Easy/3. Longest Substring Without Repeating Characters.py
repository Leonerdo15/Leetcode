# chat says ict is a little bit better because it can remember the last position of every char no need to go one by one

class Solution(object):
    def lengthOfLongestSubstring(self, s):
        crr_string = set()
        biggest_string_size = 0

        left = 0

        for right in range(len(s)):

            while s[right] in crr_string:
                crr_string.remove(s[left])
                left += 1

            crr_string.add(s[right])

            biggest_string_size = max(
                biggest_string_size,
                right - left + 1
            )

        return biggest_string_size


if __name__ == "__main__":
    sol = Solution()
    s = "pwwkew"
    print(sol.lengthOfLongestSubstring(s))