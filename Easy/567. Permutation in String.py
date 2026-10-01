class Solution(object):
    def checkInclusion(self, s1, s2):
        k  = len(s1)
        left = 0
        current_str = ""

        for i in range(len(s2)):
            current_str += s2[i]

            if len(current_str) > k:
                current_str = current_str[1:]

            if len(current_str) == k and sorted(current_str) == sorted(s1):
                return True

        return False


if __name__ == '__main__':
    s1 = "ab"
    s2 = "eidbaooo"
    solution = Solution()
    result = solution.checkInclusion(s1, s2)
    print(result)