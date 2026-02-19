from insightface.app import FaceAnalysis
app = FaceAnalysis(name="buffalo_l", root="/app/models", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=-1, det_size=(640, 640))
print("buffalo_l model downloaded successfully")
