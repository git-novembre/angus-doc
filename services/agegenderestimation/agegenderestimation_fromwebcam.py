# -*- coding: utf-8 -*-
import cv2
import numpy as np
import StringIO
import angus

def main(stream_index):
    camera = cv2.VideoCapture(stream_index)
    camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.cv.CV_CAP_PROP_FPS, 10)

    if not camera.isOpened():
        print("Cannot open stream of index {}".format(stream_index))
        exit(1)

    print("Video stream is of resolution {} x {}".format(camera.get(3), camera.get(4)))

    conn = angus.connect()
    service = conn.services.get_service("age_and_gender_estimation", version=1)
    service.enable_session()

    while camera.isOpened():
        ret, frame = camera.read()

        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, buff = cv2.imencode(".jpg", gray,  [cv2.IMWRITE_JPEG_QUALITY, 80])
        buff = StringIO.StringIO(np.array(buff).tostring())

        job = service.process({"image": buff})
        res = job.result

        for face in res['faces']:
            x, y, dx, dy = face['roi']
            age = face['age']
            gender = face['gender']

            cv2.rectangle(frame, (x, y), (x+dx, y+dy), (0,255,0))
            cv2.putText(frame, "(age, gender) = ({:.1f}, {})".format(age, gender),
                        (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (255, 255, 255))

        cv2.imshow('original', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    service.disable_session()

    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    ### Web cam index might be different from 0 on your setup.
    ### To grab a given video file instead of the host computer cam, try:
    ### main("/path/to/myvideo.avi")
    main(0)
