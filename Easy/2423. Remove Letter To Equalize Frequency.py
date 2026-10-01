class Solution:
    def equalFrequency(self, word):

        freq = {}

        for char in word:
            if char in freq:
                freq[char] += 1
            else:
                freq[char] = 1

        freq_of_freq = {}

        for quant in freq.values():
            if quant in freq_of_freq:
                freq_of_freq[quant] += 1
            else:
                freq_of_freq[quant] = 1

        print(freq_of_freq)

        if len(freq_of_freq) == 1:
            frequency, count = list(freq_of_freq.items())[0]
            return frequency == 1 or count == 1

        if len(freq_of_freq) != 2:
            return False

        (freq1, count1), (freq2, count2) = sorted(freq_of_freq.items())

        return (freq1 == 1 and count1 == 1) or (freq2 == freq1 + 1 and count2 == 1)


if __name__ == "__main__":
    sol = Solution()
    word = "aabbccd"
    print(sol.equalFrequency(word))


