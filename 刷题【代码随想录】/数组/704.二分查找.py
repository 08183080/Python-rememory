from typing import List

class Solution:
    def search(self, nums: List[int], target: int) -> int:
        l, r = 0, len(nums)  # [l, r)
        while l < r:
            mid = (l + r)//2
            if nums[mid] == target:
                return mid
            elif nums[mid] > target:
                r = mid
            else:
                l = mid + 1
        return -1 

if __name__ == "__main__":
    sol = Solution()
    print(sol.search([-1,0,3,5,9,12], 9))  # Output: 4
    print(sol.search([-1,0,3,5,9,12], 2))  # Output: -1