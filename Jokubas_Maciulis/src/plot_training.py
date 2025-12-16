import matplotlib.pyplot as plt

def plot_training_history(history, save_path=None):
    
    fig, (ax1, ax2) = plt.subplots(ncols=2, nrows=1, figsize=(14, 5))
    plt.subplots_adjust(wspace=0.2)

    ax1.plot(history.history["accuracy"], label="Training set", c="k", lw=3)
    ax1.plot(history.history["val_accuracy"], label="Validation set")
    ax1.set_xlabel("Number of passed epochs")
    ax1.set_ylabel("Accuracy")
    ax1.legend()
    ax1.grid()

    ax2.plot(history.history["loss"], label="Training set", c="k", lw=3)
    ax2.plot(history.history["val_loss"], label="Validation set")
    ax2.set_xlabel("Number of passed epochs")
    ax2.set_ylabel("Loss")
    ax2.legend()
    ax2.grid()
    
    if save_path:
        plt.savefig(save_path, dpi=300)
    
    plt.show()

def plot_auc(history, save_path=None):
    plt.figure(figsize=(7,5))
    plt.plot(history.history["auc"], label="Training AUC", lw=2)
    plt.plot(history.history["val_auc"], label="Validation AUC", lw=2)
    plt.xlabel("Epochs")
    plt.ylabel("AUC")
    plt.legend()
    plt.grid()
    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.show()
