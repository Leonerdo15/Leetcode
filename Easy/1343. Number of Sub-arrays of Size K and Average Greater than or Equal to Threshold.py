class Solution(object):
    def numOfSubarrays(self, arr, k, threshold):
        total_arr = 0
        curr_sum = 0

        for i in range(k):
            curr_sum += arr[i]

        if curr_sum / k >= threshold:
            total_arr += 1


        for i in range(k, len(arr)):
            curr_sum += arr[i]
            curr_sum -= arr[i - k]

            if curr_sum / k >= threshold:
                total_arr += 1

        return total_arr


if __name__ == "__main__":
    sol = Solution()
    arr = [11,13,17,23,29,31,7,5,2,3]
    k = 3
    threshold = 5
    print(sol.numOfSubarrays(arr, k, threshold))