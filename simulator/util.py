def get_bin_idx(bins, x):
    """ Get the bin that x would be allocated, cumulatively """
    x = x % sum(bins)
    idx = 0
    while x > 0:
        x -= bins[idx]
        idx += 1
    return idx
