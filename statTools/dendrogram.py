from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import numpy as np

doShow = True


# generate two clusters: a with 100 points, b with 50:
np.random.seed(4711)  # for repeatability of this tutorial
a = np.random.multivariate_normal([10, 0], [[3, 1], [1, 4]], size=[100,])
b = np.random.multivariate_normal([0, 20], [[3, 1], [1, 4]], size=[50,])
X = np.concatenate((a, b),)
print X.shape, 'is the shape of X'  # 150 samples with 2 dimensions
if doShow:
    plt.scatter(X[:,0], X[:,1])
    plt.show()
    doShow = False

# generate the linkage matrix
"""
'ward' causes linkage() to use the Ward variance minimization algorithm.
I think it's a good default choice, but it never hurts to play around with
some other common linkage methods like 'single', 'complete', 'average', ...
and the different distance metrics like 'euclidean' (default), 'cityblock'
aka Manhattan, 'hamming', 'cosine'... if you have the feeling that your
data should not just be clustered to minimize the overall intra cluster
variance in euclidean space. For example, you should have such a weird
feeling with long (binary) feature vectors (e.g., word-vectors in text
clustering).
"""
Z = linkage(X, 'ward')



from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist

c, coph_dists = cophenet(Z, pdist(X))

if doShow:
    idxs = [33, 68, 62]
    plt.figure(figsize=(10, 8))
    plt.scatter(X[:,0], X[:,1])  # plot all points
    plt.scatter(X[idxs,0], X[idxs,1], c='r')  # plot interesting points in red again
    plt.show()


if doShow:
    idxs = [33, 68, 62]
    plt.figure(figsize=(10, 8))
    plt.scatter(X[:,0], X[:,1])
    plt.scatter(X[idxs,0], X[idxs,1], c='r')
    idxs = [15, 69, 41]
    plt.scatter(X[idxs,0], X[idxs,1], c='y')
    plt.show()

# calculate full dendrogram
if doShow:
    plt.figure(figsize=(25, 10))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    dendrogram(
        Z,
        leaf_rotation=90.,  # rotates the x axis labels
        leaf_font_size=8.,  # font size for the x axis labels
    )
    plt.show()

if doShow:
    plt.title('Hierarchical Clustering Dendrogram (truncated)')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    dendrogram(
        Z,
        truncate_mode='lastp',  # show only the last p merged clusters
        p=12,  # show only the last p merged clusters
        show_leaf_counts=False,  # otherwise numbers in brackets are counts
        leaf_rotation=90.,
        leaf_font_size=12.,
        show_contracted=True,  # to get a distribution impression in truncated branches
    )
    plt.show()


def fancy_dendrogram(*args, **kwargs):
    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title('Hierarchical Clustering Dendrogram (truncated)')
        plt.xlabel('sample index or (cluster size)')
        plt.ylabel('distance')
        for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c=c)
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                             textcoords='offset points',
                             va='top', ha='center')
        if max_d:
            plt.axhline(y=max_d, c='k')
    return ddata

fancy_dendrogram(
    Z,
    truncate_mode='lastp',
    p=12,
    leaf_rotation=90.,
    leaf_font_size=12.,
    show_contracted=True,
    annotate_above=10,  # useful in small plots so annotations don't overlap
)
plt.show()