class Solution(object):
    def totalFruit(self, fruits):
        baskets = {}
        left = 0
        max_fruits = 0

        for i in range(len(fruits)):

            current_fruit = fruits[i]
            if current_fruit in baskets:
                baskets[current_fruit] += 1
            else:
                baskets[current_fruit] = 1

            while len(baskets) > 2:
                baskets[fruits[left]] -= 1


                if baskets[fruits[left]] == 0:
                    del baskets[fruits[left]]

                left += 1

            sum_basket = sum(baskets.values())
            if sum_basket > max_fruits:
                max_fruits = sum_basket

        return max_fruits


if __name__ == '__main__':
    fruits =[1,2,1]
    solution = Solution()
    result = solution.totalFruit(fruits)
    print(result)  # Output: 3