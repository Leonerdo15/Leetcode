class Solution(object):
    def findMaxAverage(self, nums, k):
        total = 0

        for i in range(k):
            total += nums[i]

        max_value = total

        for i in  range(k, len(nums)):

            total += nums[i]
            total -= nums[i - k]

            if total > max_value:
                max_value = total

        return float(max_value) / k


if __name__ == "__main__":
    sol = Solution()
    nums = [1,12,-5,-6,50,3]
    k = 4
    print(sol.findMaxAverage(nums, k))

