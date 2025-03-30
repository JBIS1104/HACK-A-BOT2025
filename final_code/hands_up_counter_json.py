from modlib.apps import Annotator
from modlib.devices import AiCamera
from modlib.models.zoo import Posenet
import cv2

# Initialize camera and model
device = AiCamera()
model = Posenet()
device.deploy(model)

# Initialize annotator for drawing on frames
annotator = Annotator()

# Define skeleton connections for visualization
skeleton = [
    [5, 7], [7, 9],    # left arm
    [6, 8], [8, 10],   # right arm
    [5, 6],            # shoulders
    [5, 11], [6, 12],  # torso
    [11, 13], [12, 14] # legs
]

# Main processing loop
with device as stream:
    for frame in stream:
        print("\nFrame Detection Details:")
        print(f"Number of poses detected: {len(frame.detections.keypoints)}")
        
        # Process detected poses
        hands_up_count = 0
        
        # Get poses with confidence above threshold
        valid_indices = frame.detections.confidence > 0.3
        
        if np.any(valid_indices):
            keypoints_array = frame.detections.keypoints[valid_indices]
            
            # Process each detected pose
            for i, keypoints in enumerate(keypoints_array):
                try:
                    # Convert 34-element array to 17x2 coordinates
                    keypoints = np.array(keypoints)
                    if len(keypoints) == 34:
                        # Reshape to (17, 2) for x,y coordinates
                        coords = keypoints.reshape(-1, 2)
                        # Add confidence scores (assuming all valid for now)
                        confidence = np.ones((17, 1)) * 0.5
                        keypoints = np.hstack((coords, confidence))
                    
                    # Draw skeleton lines connecting keypoints
                    for connection in skeleton:
                        if (keypoints[connection[0]][2] > 0.3 and 
                            keypoints[connection[1]][2] > 0.3):
                            pt1 = tuple(map(int, keypoints[connection[0]][:2]))
                            pt2 = tuple(map(int, keypoints[connection[1]][:2]))
                            cv2.line(frame.image, pt1, pt2, (255, 255, 255), 2)
                    
                    # Draw keypoints
                    for j in range(len(keypoints)):
                        x, y = int(keypoints[j][0]), int(keypoints[j][1])
                        cv2.circle(frame.image, (x, y), 4, (0, 255, 0), -1)
                    
                    # Check if hands are raised
                    if is_hands_up(keypoints):
                        hands_up_count += 1
                        # Draw indicator above head
                        head_x, head_y = int(keypoints[0][0]), int(keypoints[0][1])
                        cv2.circle(frame.image, (head_x, head_y-20), 10, (0, 255, 0), -1)
                
                except Exception as e:
                    print(f"Error processing pose {i}: {str(e)}")
                    continue
        
        # Display count of people with hands up
        total_valid = int(np.sum(valid_indices))
        attendance = (total_valid / total_student) * 100 if total_student > 0 else 0
        questions = hands_up_count
        understand = total_valid - hands_up_count
        
        data = {
            "attendance": round(attendance, 2),
            "questions": questions,
            "understand": understand
            }
            
        """
        cv2.putText(frame.image, 
                   f"Hands up: {hands_up_count}/{total_valid}", 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, 
                   (255, 255, 255), 
                   2)
        """
        cv2.putText(frame.image, 
                   f"Attendance: {attendance}%, \n Q: {hands_up_count}, \n understand: {understand}", 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   1, 
                   (255, 255, 255), 
                   2)
        # Show the annotated frame
        frame.display()
        
if __name__ == "__main__":
    app.run(host="10.209.232.184", port=5050)

