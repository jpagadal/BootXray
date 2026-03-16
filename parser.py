import re
import datetime
import sys

def process_ftrace(input_file):
    # Create the output filename with a timestamp to avoid overwriting
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ftrace_postProcess_{timestamp}.txt"
    
    # Regex pattern to match the lines that need transformation
    # Group 1: Everything up to the colon after the timestamp (e.g., "          systemd-1       [005] d....     5.376475: ")
    # Group 2: The PID/ID (trailing number in the process name) (e.g., "1")
    # Group 3: The function name inside the parentheses (e.g., "really_probe")
    # Group 4: The rest of the line after the removed section (e.g., 'dev="88e6000.phy" drv="..."')
    pattern_b = re.compile(r'^(.+?-(\d+)\s+\[\d+\].*?:\s+)\w+:\s+\((.*?)\+0[xX][0-9a-fA-F]+/0[xX][0-9a-fA-F]+\)\s+(.*)$')
    
    # Pattern to match the return of a probe, e.g. "Rreally_probe: (__driver_probe_device+0x94/0x1d8 <- really_probe)"
    # Group 1: Prefix
    # Group 2: PID
    # Group 3: Function name (right side of <-)
    pattern_e = re.compile(r'^(.+?-(\d+)\s+\[\d+\].*?:\s+)R[a-zA-Z0-9_]+:\s+\(.*<-\s+([a-zA-Z0-9_]+)\)\s*$')

    matched_lines_count = 0
    total_lines = 0

    print(f"Reading from {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                total_lines += 1
                
                match_b = pattern_b.match(line)
                if match_b:
                    prefix = match_b.group(1)
                    pid = match_b.group(2)
                    func_name = match_b.group(3)
                    rest_of_line = match_b.group(4)
                    
                    # Construct the transformed line for beginning
                    new_line = f"{prefix}tracing_mark_write: B|{pid}|{func_name} {rest_of_line}\n"
                    outfile.write(new_line)
                    matched_lines_count += 1
                    continue
                
                match_e = pattern_e.match(line)
                if match_e:
                    prefix = match_e.group(1)
                    pid = match_e.group(2)
                    func_name = match_e.group(3)
                    
                    # Construct the transformed line for end
                    new_line = f"{prefix}tracing_mark_write: E|{pid}|{func_name}\n"
                    outfile.write(new_line)
                    matched_lines_count += 1
                    continue
                
                # Write the unmodified line if no match
                outfile.write(line)
                    
        print(f"Processing complete!")
        print(f"Total lines processed: {total_lines}")
        print(f"Lines transformed: {matched_lines_count}")
        print(f"Output saved to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        sys.exit(1)

if __name__ == "__main__":
    process_ftrace("ftrace.txt")
