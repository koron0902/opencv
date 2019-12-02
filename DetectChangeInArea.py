import cv2, sys
from time import sleep


# Make base image
def Learn(_cap):
	ret, mean = _cap.read()
	for i in range(50):
		ret, tmp = _cap.read()
		mean = cv2.addWeighted(mean, 0.7, tmp, 0.3, 0)
	return mean

# Split by color
def SplitColor(_img, _color):
	b, g, r = cv2.split(_img)

	if _color == "red":
		return r
	if _color == "green":
		return g
	if _color == "blue":
		return b

	return b, g, r

# Calculate how increase the value of color
def ColorDiff(_src, _dst):
	return cv2.addWeighted(_dst, 1, _src, -1, 0)

# Convert to 2-value image
def toBinary(_img, _thresh):
	ret, binary = cv2.threshold(_img, _thresh, 255, cv2.THRESH_BINARY)
	return binary

def toGrayScale(_img):
	ret = cv2.cvtColor(_img, cv2.COLOR_BGR2GRAY)
	return ret

def main(_camera, _height, _width):
	# Open camera device
	print("initialize camera....")
	cap = cv2.VideoCapture(_camera)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, _height)
	cap.set(cv2.CAP_PROP_FRAME_WIDTH,  _width)
	cap.set(cv2.CAP_PROP_FPS, 60)

	# Failed to open
	if cap.isOpened() is False:
		print("Cannot open camera")
		sys.exit()

	print("create window....")
	cv2.namedWindow("webcam", cv2.WINDOW_AUTOSIZE)
	cv2.namedWindow("mean",   cv2.WINDOW_AUTOSIZE)
	cv2.namedWindow("diff",   cv2.WINDOW_AUTOSIZE)
	cv2.namedWindow("binary", cv2.WINDOW_AUTOSIZE)

	print("make base image....")
	mean = Learn(cap)
	cv2.imshow("mean", mean)

	while True:
		ret, frame = cap.read()
		if ret is False:
			break

		cv2.imshow("webcam", frame)

		diff = ColorDiff(SplitColor(mean, "blue"), SplitColor(frame, "blue"))
		cv2.imshow("diff", diff)

#		if len(diff.shape) == 3:
#			diff = toGrayScale(diff)

		binary = toBinary(diff, 100)

		cv2.imshow("binary", binary)

		# Change area detection(increase value of color)
		h, w = binary.shape[:2]
		for i in range(int(h / 40)):
			for j in range(int(w / 40)):
				top = 40 * i
				bottom = top + 40
				left = 40 * j
				right = left + 40
				area = binary[top : bottom , left : right]
				white = cv2.countNonZero(area)
				ratio = white / (40 * 40) * 100
				if ratio > 30:
					print("Detect on Area h:{0}-{1},w{2}-{3}".format(top, bottom, left, right))



		key = cv2.waitKey(30)
		if key == 27: # ESC
			break;
		elif key == 32: # SPACE
			mean = Learn(cap)
			cv2.imshow("mean", mean)

	cap.release()
	cv2.destroyAllWindows()

if __name__ == "__main__":
	args = sys.argv

	if "--help" in args or "-h" in args:
		print("  --cam [cameraNo]\n\tSelect camera device to capture. Default is Cam0(internal camera)")
		print("  --width [width(px)]\n\tCamera width in pixel. Default is 640px")
		print("  --height [height(px)]\n\tCamera height in pixel. Default is 480px")
		exit()

	cam = int(args[args.index("--cam") + 1]) if "--cam" in args else -1
	if cam == -1:
		cam = 0
		print("--cam option is not set. Default Camera is selected")

	width = int(args[args.index("--width") + 1]) if "--width" in args else -1
	if width == -1:
		width = 640
		print("--width option is not set. Default width(640px) is Used")

	height = int(args[args.index("--height") + 1]) if "--height" in args else -1
	if height == -1:
		height = 480
		print("--height option is not set. Default height(480px) is used")


	main(cam, height, width)
