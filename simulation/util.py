def get_bin_idx(bins, x):
    """ Get the bin that x would be allocated, cumulatively """
    x = x % sum(bins)
    idx = -1
    while x >= 0:
        x -= bins[idx]
        if x >= 0:
            idx += 1
    return idx
