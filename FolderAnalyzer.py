import os
import glob
import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

class FolderAnalyzer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.size_units = {"B": 1, "KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3, "TB": 1024 ** 4}

    def analyze_folder_size(self, size_unit):
        total_size = 0
        for path, dirs, files in os.walk(self.folder_path):
            for f in files:
                fp = os.path.join(path, f)
                total_size += os.path.getsize(fp)

        if size_unit in self.size_units:
            total_size /= self.size_units[size_unit]
        else:
            size_unit = "B" 

        return round(total_size, 2), size_unit

    def analyze_file_types(self, size_unit, min_size, max_size):
        file_list = []
        if size_unit not in self.size_units:
            size_unit = "B" 

        for file in glob.iglob(self.folder_path + '/**/*', recursive=True):
            if os.path.isfile(file):
                file_extension = os.path.splitext(file)[1].lower()
                file_mod_time = os.path.getmtime(file)
                file_mod_date = datetime.datetime.fromtimestamp(file_mod_time)
                file_size = os.path.getsize(file)

               
                if size_unit in self.size_units:
                    file_size /= self.size_units[size_unit]
                else:
                    size_unit = "B"  

                
                if (min_size is None or min_size <= file_size) and (max_size is None or file_size <= max_size):
                    file_info = (os.path.basename(file), round(file_size, 2), size_unit, file_extension, file_mod_date.strftime('%Y-%m-%d %H:%M:%S'))
                    file_list.append(file_info)

        return file_list

    def delete_file(self, file_name):
        file_path = os.path.join(self.folder_path, file_name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)

    def create_file_with_extension(self, file_name, file_extension, content=""):
        file_path = os.path.join(self.folder_path, f"{file_name}.{file_extension}")
        with open(file_path, 'w') as file:
            file.write(content)

    def search_file_by_name(self, search_query):
        file_list = []
        for file in glob.iglob(self.folder_path + '/**/*', recursive=True):
            if os.path.isfile(file):
                file_name = os.path.basename(file)
                if search_query.lower() in file_name.lower():
                    file_extension = os.path.splitext(file)[1].lower()
                    file_mod_time = os.path.getmtime(file)
                    file_mod_date = datetime.datetime.fromtimestamp(file_mod_time)
                    file_size = os.path.getsize(file)

                    file_info = (file_name, round(file_size, 2), "B", file_extension, file_mod_date.strftime('%Y-%m-%d %H:%M:%S'))
                    file_list.append(file_info)

        return file_list

@app.route("/delete", methods=["POST"])
def delete_file():
    folder_path = request.form.get("folder_path")
    size_unit = request.form.get("size_unit")
    min_size = float(request.form.get("min_size")) if request.form.get("min_size") else None
    max_size = float(request.form.get("max_size")) if request.form.get("max_size") else None
    file_name_to_delete = request.form.get("file_name")

    analyzer = FolderAnalyzer(folder_path)

   
    analyzer.delete_file(file_name_to_delete)

   
    size, size_unit = analyzer.analyze_folder_size(size_unit)
    file_list = analyzer.analyze_file_types(size_unit, min_size, max_size)

    return render_template("result.html", size=size, size_unit=size_unit, file_list=file_list)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    folder_path = request.form.get("folder_path")
    size_unit = request.form.get("size_unit")
    min_size = float(request.form.get("min_size")) if request.form.get("min_size") else None
    max_size = float(request.form.get("max_size")) if request.form.get("max_size") else None
    analyzer = FolderAnalyzer(folder_path)

    size, size_unit = analyzer.analyze_folder_size(size_unit)
    file_list = analyzer.analyze_file_types(size_unit, min_size, max_size)

    return render_template("result.html", size=size, size_unit=size_unit, file_list=file_list)

@app.route("/create_file_with_extension", methods=["POST"])
def create_file_with_extension():
    folder_path = request.form.get("folder_path")
    file_name = request.form.get("file_name")
    file_extension = request.form.get("file_extension")
    content = request.form.get("file_content")

    analyzer = FolderAnalyzer(folder_path)

   
    analyzer.create_file_with_extension(file_name, file_extension, content)

    
    return redirect(url_for("index"))

@app.route("/search_file", methods=["POST"])
def search_file():
    folder_path = request.form.get("folder_path")
    search_query = request.form.get("search_query")

    analyzer = FolderAnalyzer(folder_path)

    file_list = analyzer.search_file_by_name(search_query)

    return render_template("result.html", file_list=file_list)

if __name__ == "__main__":
    app.run(debug=True)
