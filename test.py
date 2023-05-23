import json

def parse_sse_data(sse_line):
    prefix = "data: "
    if sse_line.startswith(prefix):
        json_line = sse_line[len(prefix):]
        return json.loads(json_line)
    else:
        raise ValueError("Invalid SSE line")

sse_line = 'data: {"status": "working", "progress": {"total": 4, "current": 0}, "data": null}'
data = parse_sse_data(sse_line)
print(data)
