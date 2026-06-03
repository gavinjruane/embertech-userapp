import subprocess
from pathlib import Path

# pip install svg2gcode ezdxf

input_file = Path("input.dxf")
output_file = Path("output.ngc")

subprocess.run(
    ["python", "-m", "svg2gcode", str(input_file), "-o", str(output_file)],
    check=True,
)

print("[DONE] Output:", output_file)
