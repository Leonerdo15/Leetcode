class Solution(object):
    def minSubArrayLen(self, target, nums):
        smallest_size = float("inf")
        left = 0
        total = 0

        for i in range(len(nums)):
            total += nums[i]

            while total >= target:
                smallest_size = min(smallest_size, i - left + 1)

                total -= nums[left]
                left += 1


        if smallest_size == float("inf"):
            return 0
        else:
            return smallest_size

if __name__ == '__main__':
    sol = Solution()
    target = 11
    nums = [1,2,3,4,5]
    value = sol.minSubArrayLen(target, nums)
    print(value)

