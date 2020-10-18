import os
import sys
import moviepy
import moviepy.editor
import subprocess
import argparse
import datetime

def split_video(path:str, video_st_time:datetime.datetime, max_len_segment:datetime.datetime, output_path:str, verbose=0) -> list:
    """
    Splits a given video in path into smaller parts, based on video_st_time, max_len_segment.
    Then those new videos are saved in the location specified in output_path.

    Parameters
    ----------
    path: str
        String with the path location of the original video.
    video_st_time: datetime
        Starting time of the video. Everything in the video before this
        time is discarded.
    max_len_segment: datetime
        The length of each output video.
    output_path: str
        String with the output location of the videos.
    verbose: int
        Sets the screen printout to 0.

    Returns
    -------
    A list of tuples that consists of each new video's starting time and
    a path to the video's saved location, i.e. (t:datetime, path: str).
    """

    if not os.path.isfile(path):
        return []

    clips_array = []
    video_st_time=int(datetime.timedelta(hours=video_st_time.hour, minutes=video_st_time.minute, seconds=video_st_time.second).total_seconds())
    max_len_segment=int(datetime.timedelta(hours=max_len_segment.hour, minutes=max_len_segment.minute, seconds=max_len_segment.second).total_seconds())

    result = subprocess.Popen(['hachoir-metadata', path],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    results = result.stdout.read().decode('utf-8').split('\r\n')

    original_video = moviepy.editor.VideoFileClip(path)
    video_duration = int(original_video.duration)

    if (int(video_st_time) >= video_duration):
        return []

    creation_date=datetime.datetime.now()
    for item in results:
        if item.startswith('- Creation date: '):
            creation_date = datetime.datetime.strptime(item.lstrip('- Creation date: '), "%Y-%m-%d %H:%M:%S")

    while (int(video_st_time) + int(max_len_segment) < video_duration):
        clip = original_video.subclip(video_st_time, video_st_time + max_len_segment)

        subclip_date= creation_date + datetime.timedelta(seconds=video_st_time)
        subclip_date_formatted= subclip_date.strftime("%Y%m%d%H%M%S") +"_.mp4"
        clips_array.append((subclip_date,
                            output_path + '/' +subclip_date_formatted))
        clip.write_videofile(
            os.path.join(output_path, subclip_date_formatted), audio=True, fps=original_video.fps)
        video_st_time += max_len_segment

    clip = original_video.subclip(video_st_time, video_duration)

    subclip_date= creation_date + datetime.timedelta(seconds=video_st_time)
    subclip_date_formatted = subclip_date.strftime("%Y%m%d%H%M%S")+ "_.mp4"
    clips_array.append((subclip_date,
                        output_path + '/' + subclip_date_formatted))
    clip.write_videofile(
        os.path.join(output_path, subclip_date_formatted), audio=True,
        fps=original_video.fps)

    original_video.close()
    return clips_array

def main():
    """
    main method of split_video(), to be used as CLI interface.
    After verifying that enough arguments were passed and their validity,
    calls split_video.

    Returns
    -------
    A list of tuples that consists of each new video's starting time and
    a path to the video's saved location, i.e. (t:datetime, path: str).
    """
    parser = argparse.ArgumentParser(description="split video")
    parser.add_argument('input_dir', nargs='?', help="Input directory", type=str)
    parser.add_argument('start_time',nargs='?', help="Starting time of the video",
                        type=str)
    parser.add_argument('max_length_of_video', nargs='?', help="The length of each output video",
                        type=str)
    parser.add_argument('output_dir', nargs='?', help="Output directory", type=str)
    args = vars(parser.parse_args())

    result_list=[]

    if os.path.isdir(args['input_dir']):
        ext = [".3g2", ".3gp", ".asf", ".asx", ".avi", ".flv", ".m2ts", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".rm",
               ".swf", ".vob", ".wmv"]
        for file in os.listdir(args['input_dir']):
            if file.endswith(tuple(ext)):
                result_list.extend(split_video(args['input_dir'] + "/" + file, datetime.datetime.strptime(args['start_time'], "%H:%M:%S"),
                                               datetime.datetime.strptime(args['max_length_of_video'], "%H:%M:%S"), args['output_dir']))
    else:
        print('Not a valid directory path')
        sys.exit()

    return result_list

if __name__ == "__main__":
    main()
