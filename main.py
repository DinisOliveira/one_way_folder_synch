import os
import hashlib
import shutil
import logging
import argparse
import time

#Function to Generate hashes for files in a directory and its subdirectories, it assigns eachs hash to a key.
#And each filename/s (in case it´s the source folder) or each rel path(in case there are subdirectories of source populated with files) associated with that hash to the value/s of that key in a dict.         
def dict_hashes(path, hash_dict_main, hash_dict_sub):
    #Using os.listdir to be more eficient in case source has no subdirectories:
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            #Calculates md5 hash for files in the source directory:
            md5 = hashlib.md5()
            with open(file_path, 'rb') as file:
                #Reading by chuncks in case there are big files:
                while chunck := file.read(8192):
                    md5.update(chunck)
            hash = md5.hexdigest()
            #Updates dictionary fot the source directory:
            if hash in hash_dict_main:
                if filename not in hash_dict_main[hash]:
                    hash_dict_main[hash].append(filename)
             
            else:
                hash_dict_main[hash] = [filename]


        elif os.path.isdir(file_path):
            # Using os.walk to list through directories in the case of subdirectories. 
            for dir, _, files in os.walk(file_path):

                for name in files:
                    rel_sub_path_file = os.path.relpath(os.path.join(dir, name), path)
                    sub_file_path = os.path.join(dir, name)
                    if os.path.isfile(sub_file_path):
                        #Calculates md5 hash for files in the source subdirectories:
                        md5 = hashlib.md5()

                        with open(sub_file_path, 'rb') as file:
                            #Reading by chuncks in case there are big files:
                            while chunck := file.read(8192):
                                md5.update(chunck)
                        hash = md5.hexdigest()
                        #Updates dictionary fot the source subdirectories:
                        if hash in hash_dict_sub:
                            hash_dict_sub[hash].append(rel_sub_path_file)
                        else:
                            hash_dict_sub[hash] = [rel_sub_path_file]
                
#Lists directories and files, associating in a dictionary each directory name to their rel file paths:
def ls_dir(path, sub_dir_files):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isdir(file_path):

            for dir, _, files in os.walk(path):
            
                relative_dir = os.path.relpath(dir, path)
                if relative_dir == ".":
                    relative_dir = "source"
                sub_dir_files[relative_dir] = []

                for file in files:
                        relative_path = os.path.relpath(os.path.join(dir, file), path)                      
                        sub_dir_files[relative_dir].append(relative_path)
        

#Creates and removes sudirectories in destination based on if they exist or not in source:
def create_remove_sub_folders(source_dirs, replica_dirs, s_path, d_path):

    if source_dirs != replica_dirs:
        source_dirs.pop('source', None)
        replica_dirs.pop('source', None)

        for sub_dir in source_dirs.keys():  
            destination_dir_path = os.path.join(d_path, sub_dir)
                  
            if not os.path.exists(destination_dir_path):
                os.mkdir(destination_dir_path)

                log_message = (f"created {destination_dir_path}")
                logging.info(log_message)
                print(log_message)

        for sub_dir in replica_dirs.keys():
            source_dir_path = os.path.join(s_path, sub_dir)
            remove_path = os.path.join(d_path, sub_dir)
            
            if not os.path.exists(source_dir_path):
                shutil.rmtree(remove_path)
                log_message = f"Removed {remove_path}"
                logging.info(log_message)
                print(log_message)

    else:
        #print("Subdirectory folders match")
        return None

#Copies files in source root directory that are not in replica root directory.
def copy_source_files(source_hashes, dest_hashes, s_path, d_path):
    if source_hashes == dest_hashes:
        #print("Nothing to Modify in main folder")
        return None

    else:
        #print("There are changes")

        #If the hash for a file/s doesn´t exist at all in replica root directory it copies all the files associated with that hash in source root to replica root:
        for hash, file_names in source_hashes.items():
            if hash not in dest_hashes:
                print(hash)
                for file_name in file_names:
                    source_file_path = os.path.join(s_path, file_name)
                    dest_file_path = os.path.join(d_path, file_name)

                    if not os.path.exists(dest_file_path):
                        shutil.copy2(source_file_path, dest_file_path)
                        log_message =f"copied {source_file_path} to {dest_file_path}"
                        logging.info(log_message)
                        print(log_message)

            else:
                #If the hash already exists in replica root(meaning there are already files with that hash in replica) it copies only the files that are not already in replica.
                dest_files = dest_hashes[hash]
                for file_name in file_names:
                    if file_name not in dest_files:
                        source_file_path = os.path.join(s_path, file_name)
                        dest_file_path = os.path.join(d_path, file_name)
                        if not os.path.exists(dest_file_path):
                            shutil.copy2(source_file_path, dest_file_path)
                            log_message = f"copied {source_file_path} to {dest_file_path}"
                            logging.info(log_message)
                            print(log_message)

#Copies files in source subdirectories directory that are not in replica subdirectories:
#Copies files in source subdirectories directory that are not in replica subdirectories:
def copy_sub_files(source_sub_hashes, dest_sub_hashes, s_path, d_path):
    if source_sub_hashes == dest_sub_hashes:
        #print("Nothing to Modify in sub directory files")
        return None

    else:
        #print("There are changes in sub directory files:")
          #If the hash for a file/s doesn´t exist at all in replica's subdirectories it copies all the files associated with that hash in source subdirectories to their respective path in replica subdirectories:
        for hash, file_names in source_sub_hashes.items():
            if hash not in dest_sub_hashes:
                print(hash)
                for file_name in file_names:
                    source_file_path = os.path.join(s_path, file_name)
                    dest_file_path = os.path.join(d_path, file_name)

                    if not os.path.exists(dest_file_path):
                        shutil.copy2(source_file_path, dest_file_path)
                        log_message =f"copied {source_file_path} to {dest_file_path}"
                        logging.info(log_message)
                        print(log_message)
            else:
                #If the hash for the file/s already exists in replica subdirectories(meaning there are already files with that hash in replica subdirectories) it copies only the files that are not already in replica.
                dest_files = dest_sub_hashes[hash]
                for file_name in file_names:
                    if file_name not in dest_files:
                        source_file_path = os.path.join(s_path, file_name)
                        dest_file_path = os.path.join(d_path, file_name)
                        if not os.path.exists(dest_file_path):
                            shutil.copy2(source_file_path, dest_file_path)
                            log_message = f"copied {source_file_path} to {dest_file_path}"
                            logging.info(log_message)
                            print(log_message) 



#Removes files from replica root directory that are not in source root directory:
def remove_source_files(source_hashes, dest_hashes, s_path, d_path):
    ...
    for hash, file_names in dest_hashes.items():
                if hash not in source_hashes:
                    #If the hash for a file/s doesn´t exist at all in source root directory it removes all the files associated with that hash in replica root directory:
                    for file_name in file_names:
                        remove_path = os.path.join(d_path, file_name)
                        
                        if os.path.exists(remove_path):
                            os.remove(remove_path)
                            log_message =f"removed {remove_path}"
                            logging.info(log_message)
                            print(log_message)

                else:
                    #If the hash exists in source root directory, it removes only the files that are not at all in source root directory:
                    source_files = source_hashes[hash]
                    for file_name in file_names:
                        if file_name not in source_files:
                            source_file_path = os.path.join(s_path, file_name)
                            remove_path = os.path.join(d_path, file_name)
                            if not os.path.exists(source_file_path):
                                os.remove(remove_path)
                                log_message= f"removed {remove_path}"
                                logging.info(log_message)
                                print(log_message)

                
# Removes files from replica´s subdirectories that are not in source´s respective subdirectories.
def remove_sub_files(source_sub_hashes, dest_sub_hashes, s_path, d_path):

    if source_sub_hashes == dest_sub_hashes:
        #print("Nothing to remove in replica sub directory files")
        return None

    else:
        #print("Files to remove in replica sub directories")
        for hash, file_names in dest_sub_hashes.items():
            if hash not in source_sub_hashes:
                #If the hash for a file/s doesn´t exist at all in source subdirectories it removes all the files associated with that hash in replica subdirectories:

                for f_path in file_names:
                    remove_path = os.path.join(d_path, f_path)
                    
                    if os.path.exists(remove_path):
                        os.remove(remove_path)
                        log_message = f"removed: {remove_path}"
                        logging.info(log_message)
                        print(log_message)

            else:
                #If the hash exists in source subdirectories, it removes from replica subdirectories only the files that are not at all in source subdirectories:
                source_files = source_sub_hashes[hash]
                for file_name in file_names:
                    if file_name not in source_files:
                        source_file_path = os.path.join(s_path, file_name)
                        remove_path = os.path.join(d_path, file_name)

                        if not os.path.exists(source_file_path):
                            if os.path.exists(remove_path):
                                os.remove(remove_path)
                                log_message = f"removed {remove_path}"
                                logging.info(log_message)
                                print(log_message)

def main(source_path, replica_path, log_file_path, synch_interval):

    logging.info(f"Started: saving logs in {log_file_path}")

    if not os.path.exists(replica_path):
        os.makedirs(replica_path)
        logging.info(f"Created {replica_path}")
    
    if not os.path.exists(source_path):
        raise argparse.ArgumentError(None, "The source directory doesn't exist")
    
    
    while True:

        try:
            source_path_hashes = {}
            source_path_sub_hashes = {}
            source_sub_dir_files = {}
            dest_path_hashes = {}
            dest_path_sub_hashes = {}
            replica_sub_dir_files = {}

            #Assings each hash to the relative file path or paths for each file in root folder and subfolders.
            dict_hashes(source_path, source_path_hashes, source_path_sub_hashes)
            dict_hashes(replica_path, dest_path_hashes, dest_path_sub_hashes )
            #print(source_path_sub_hashes)

            #Assings each directory in subdirectories to their file/s rel path/s
            ls_dir(source_path, source_sub_dir_files)
            ls_dir(replica_path, replica_sub_dir_files)

            #Creates subdirectories in replica in case they exist in source and are not already in replica. 
            #Removes subdirectories of replica in case they don´t exist in source.
            create_remove_sub_folders(source_sub_dir_files, replica_sub_dir_files, source_path, replica_path)

            #Copies the files from source's root directory that are not already in replica's root directory.
            copy_source_files(source_path_hashes, dest_path_hashes, source_path, replica_path)

            #Copies the files from source's subdirectories that are not already in replica´s subdirectories.
            copy_sub_files(source_path_sub_hashes, dest_path_sub_hashes, source_path, replica_path)

            source_path_sub_hashes = {}
            dest_path_sub_hashes = {}
            dict_hashes(source_path, source_path_hashes, source_path_sub_hashes)
            dict_hashes(replica_path, dest_path_hashes, dest_path_sub_hashes )

            #Removes files from replica root directory that are not in source root directory.
            remove_source_files(source_path_hashes, dest_path_hashes, source_path, replica_path)
            remove_sub_files(source_path_sub_hashes, dest_path_sub_hashes, source_path, replica_path)
            time.sleep(synch_interval)

        except KeyboardInterrupt:
            print("Program stopped by the user")
            raise SystemExit
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description= "Program to synch folders:")
    parser.add_argument("--source_path", type=str, default="source", help="Path to Source")
    parser.add_argument("--replica_path", type=str, default="replica", help="Path to Replica")
    parser.add_argument("--log_file_path", type=str, default="log_file.txt", help="Path to Log File")
    parser.add_argument("--synch_interval", type=int, default=60, help="Time interval for synching")
    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file_path,format='%(asctime)s %(message)s',filemode='w', level=logging.INFO)

    main(args.source_path, args.replica_path, args.log_file_path,  args.synch_interval)

