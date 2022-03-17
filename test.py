nums1 = [1,2,3,0,0,0]
nums2 = [4,5,6]
m=3
n=3

def main(nums1, m, nums2, n) -> None:
    """
        Do not return anything, modify nums1 in-place instead.
        """
    temp = []
    i, j = 0, 0
    while m > i or n > j:
        if i == m:
            temp.append(nums2[j])
            j += 1
        elif j == n:
            temp.append(nums1[i])
            i += 1
        elif nums1[i] > nums2[j]:
            temp.append(nums2[j])
            j += 1
        else:
            temp.append(nums1[i])
            i += 1
    nums1 = temp
    print(nums1)

if __name__ =='__main__':
    main(nums1,m,nums2,n)
