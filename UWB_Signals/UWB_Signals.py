import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares

# Valid Position for random Tag Location
#valid_positions = np.load("valid_positions.npy")

class UWB_Generator:

    def __init__(self):
        self.tag_true = None
        self.tag_est = None
        self.error = None

        # Placeholder Anchors  
        self.anchors = np.array([
            [],
            [],
            [],
            []
        ])

    def set_anchors(self, coords):
        self.anchors = np.array(coords, dtype=float)

    def moving_signal(self):
        for i in range(1,np.random.randint(20)):
            self.random_signal()
    
    def random_signal(self):
            if self.anchors.size ==0:
                print("No Anchors Selectet yet")
            else:
                # Constants
                c = 3e8  # speed of light (m/s)
                valid_positions = np.load("valid_positions.npy")
                # Anchor positions (in pixels)
                anchors = self.anchors

                # True tag position

                idx = np.random.randint(len(valid_positions))
                self.tag_true = valid_positions[idx]

                # Generate true distances
                distances = np.linalg.norm(anchors - self.tag_true, axis=1)

                # Calculate TDoA (relative to anchor 0)
                tdoa = (distances - distances[0]) / c

                # Add noise (timing noise)
                noise_std = 1e-10  # ~0.1 ns
                noise = np.random.normal(0, noise_std, size=tdoa.shape)
                tdoa_noisy = tdoa + noise

                # Convert to distance differences
                delta_d = c * tdoa_noisy

                # TDoA residuals
                
                def tdoa_residuals(pos, anchors, delta_d):
                    x, y = pos
                    d = np.linalg.norm(anchors - np.array([x, y]), axis=1)

                    residuals = []
                    for i in range(1, len(anchors)):
                        residuals.append(d[i] - d[0] - delta_d[i])

                    return residuals

                # Solve using least squares
                initial_guess = np.array([5.0, 5.0])

                result = least_squares(
                    tdoa_residuals,
                    initial_guess,
                    args=(anchors, delta_d)
                )

                self.tag_est = result.x

                # Error calculation
                self.error = np.linalg.norm(self.tag_est - self.tag_true)

                
                print("True Position     :", self.tag_true)
                print("Estimated Position:", self.tag_est)
                print("Position Error (m):", self.error)
                """
                # Plot (debug only)

                plt.figure()

                # Anchors
                plt.scatter(anchors[:, 0], anchors[:, 1], marker='^', label='Anchors')

                # True position
                plt.scatter(self.tag_true[0], self.tag_true[1], marker='o', label='True Tag')

                # Estimated position
                plt.scatter(self.tag_est[0], self.tag_est[1], marker='x', label='Estimated Tag')

                # Draw lines to anchors (optional)
                for anchor in anchors:
                    plt.plot([self.tag_true[0], anchor[0]], [self.tag_true[1], anchor[1]], linestyle='--', linewidth=0.5)

                plt.title("UWB TDoA Localization")
                plt.xlabel("X (m)")
                plt.ylabel("Y (m)")
                plt.legend()
                plt.grid()

                plt.axis('equal')
                plt.show()
                """
if __name__ =="__main__":
    gen = UWB_Generator()
    gen.random_signal()
    #gen.moving_signal()