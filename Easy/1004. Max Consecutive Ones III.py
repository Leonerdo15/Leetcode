from collections import deque

# Cht way time is the same O(n) but space is O(k) and not just O(1)
# expand right
#
# if you see 0:
#     zero_count += 1
#
# while zero_count > k:
#     if left is 0:
#         zero_count -= 1
#     move left
#
# update maximum window size

class Solution(object):
    def longestOnes(self, nums, k):

        # store index when you see a 0
        zeros_index = deque()
        left = 0
        max_sequence = 0

        total = 0
        for i in range(len(nums)):

            if nums[i] == 1:
                total += 1
            else:
                if len(zeros_index) < k:
                    zeros_index.append(i)
                    total += 1
                elif len(zeros_index) >= k and len(zeros_index) != 0:
                    total -= (zeros_index[0] + 1) - left
                    left = zeros_index[0] + 1

                    zeros_index.popleft()
                    zeros_index.append(i)

                    total += 1
                else:
                    total = 0
                    left = i + 1

            if total > max_sequence:
                max_sequence = total

        return max_sequence




if __name__ == '__main__':
    sol = Solution()
    nums = [1,1,1,0,0,0,1,1,1,1,0]
    k = 2
    value = sol.longestOnes(nums, k)
    print(value)