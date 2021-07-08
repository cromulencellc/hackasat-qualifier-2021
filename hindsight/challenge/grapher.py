import matplotlib.pyplot as plt
from matplotlib import cm, colors

def create_3d_scatter_graph(points, name=None, vecs=None):
    fig = plt.figure(figsize=(16,16))
    ax = fig.add_subplot(111,projection='3d')

    cat = np.array(points)
    xx = cat[:,0]
    yy = cat[:,1]
    zz = cat[:,2]
    cc = None
    ax.scatter(xx,yy,zz,c=cc,cmap="Greys",s=10)

    # Reference Vectors in the x, y, and z axes
    referencevectors = np.array([ [0,0,0,1,0,0], [0,0,0,0,1,0], [0,0,0,0,0,1] ]) * 1.5
    for v in referencevectors:
        ax.quiver(v[0], v[1], v[2], v[3], v[4], v[5])

    plt.tight_layout()
    #plt.axis('off')
    plt.pause(.0001)
    plt.show()