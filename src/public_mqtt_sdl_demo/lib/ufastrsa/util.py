try:
    int.bit_length(0)

    def get_bit_length(n):
        return n.bit_length()

except:
    # Work around
    def get_bit_length(n):
        i = 0
        while n:
            n >>= 1
            i += 1
        return i
