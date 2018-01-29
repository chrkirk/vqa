import subprocess
import re


def run_command(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

def ffprobe(filename):
    info = run_command("ffprobe {} -show_format       \
                                   -show_streams      \
                                   -print_format json \
                                   -v quiet".format(filename))
    return eval(info)

def vid_duration(filename):
    return float( ffprobe(filename)["format"]["duration"] )

def vid_bitrate(filename):
    return float( ffprobe(filename)["format"]["bit_rate"] )

def vid_size(filename):
    return int( ffprobe(filename)["format"]["size"] )

def vid_width(filename):
    return int( ffprobe(filename)["streams"][0]["width"] )

def vid_height(filename):
    return int( ffprobe(filename)["streams"][0]["height"] )

def convert_resolution(input_videofile, width, height, output_videofile):
    run_command("ffmpeg           \
                -i {input}        \
                -vf scale={w}:{h} \
                {output}".format(input=input_videofile, 
                                 w=width, 
                                 h=height, 
                                 output=output_videofile))

def split_vid_into_chunks(videofile, chunk_size=10):
    def chunk_name(videofile, n):
        # a function for naming the chunks based on the original video's name
        pattern = re.compile(r"(?P<filename>\w+)\.(?P<ext>\w+)")
        matches = pattern.search(videofile).groupdict()
        return "{input_file}_part{n}.{ext}".format(input_file=matches['filename'], n=n, ext=matches['ext'])

    print("Starting to split {} ...".format(videofile))

    i = 0   # chunk number
    start = 0
    duration = vid_duration(videofile)
    while start < duration:
        chunk_filename = chunk_name(videofile, i)
        run_command("ffmpeg              \
                    -ss {chunk_start}    \
                    -t {chunk_size}      \
                    -i {input_videofile} \
                    {chunk_file}".format(chunk_start=start, 
                                         chunk_size=chunk_size, 
                                         input_videofile=videofile, 
                                         chunk_file=chunk_filename))
        print("\t ~> {}".format(chunk_filename))
        i += 1
        start += chunk_size

    print("Completed spliting {} into {} chunks each of {}secs duration.".format(videofile, i, chunk_size))

def run_tests(ref_vid):
    vid_info = {'duration': vid_duration(vid),
                'bitrate' : vid_bitrate(vid),
                'size'    : vid_size(vid),
                'width'   : vid_width(vid),
                'height'  : vid_height(vid)}
    print("Completed video info tests {}".format(vid_info))

    convert_resolution(ref_file, 426, 240, "temp.mp4")
    print("Completed convert_resolution test ... removing output file")
    run_command("rm temp.mp4")

    split_vid_into_chunks(ref_file)
    print("Completed split_vid_into_chunks test ... removing output files")
    run_command("rm {}_part*.mp4".format(ref_file.split('.')[0]))
