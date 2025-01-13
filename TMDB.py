import requests
from bs4 import BeautifulSoup
import customtkinter as ctk
from tkinter import ttk
import re

ctk.set_appearance_mode("system")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("D:/TMDB/theme/violet.json")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IMDB")
        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill='both')
        self.frames = {}
        self.soup = None
        
        for page in (page1, page2):
            page_name = page.__name__
            frame = page(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.show_frame("page1")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        
class page1(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
                   
        label = ctk.CTkLabel(self, text="Enter Movie Name", font=("Arial", 14))
        label.pack()
            
        self.entry = ctk.CTkEntry(self, width=400, height=40)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.fetch_movies)
            
        self.search_button = ctk.CTkButton(self, text="Search IMDB", command=self.fetch_movies, corner_radius=32)
        self.search_button.pack(pady=10)
        
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=20, padx=20, fill='both', expand='true')
        
                  
        columns = ("1#", "2#", "3#", "4#")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        self.table.heading("#1", text="ID")
        self.table.heading("#2", text="Title")
        self.table.heading("#3", text="Date")

        self.table.column("#1", anchor="center", width=150, stretch=False)
        self.table.column("#2", width=400, stretch=False)
        self.table.column("#3", width=200, stretch=False)
        self.table.column("#4", width=0, stretch=False)

        scrollbar = ctk.CTkScrollbar(table_frame, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)

        self.table.pack(side='left', expand=True)
        scrollbar.pack(side='right', fill='y')
        scrollbar.pack_forget()

        self.configure_treeview_style()
        self.table.bind("<ButtonRelease-1>", self.on_tree_select)
        


            
    def fetch_movies(self, event=None):
        movie_name = self.entry.get().replace(" ", "%20")
        url = f'https://www.themoviedb.org/search/movie?query={movie_name}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive'
        }
        r = requests.get(url, headers=headers)

        # Parsing the HTML
        self.controller.soup = BeautifulSoup(r.content, 'lxml')
        
        for item in self.table.get_children():
            self.table.delete(item)
        movie_details = self.controller.soup.find_all('div', {'class' : 'details'})
        if movie_details:
            for idx,movie in enumerate(movie_details, start=1):
                movie_tag = movie.find('div', {'class' : 'title'})
                movie_title_tag = movie_tag.find('h2')
                movie_date_tag = movie_tag.find('span', {'class' : 'release_date'})
                movie_title = movie_title_tag.get_text(strip=True)
                movie_date = movie_date_tag.get_text(strip=True)
                movie_link = movie_tag.find('a')['href']
                movie_id = movie_link.split('/')[2]
                
                self.table.insert("", "end", values=(idx, movie_title, movie_date, movie_id))
        else:
            self.table.insert("", "end", values=(1, "No Movies Found", "N/A"))

    def configure_treeview_style(self):
        mode = ctk.get_appearance_mode()
        style = ttk.Style()
        style.theme_use('clam')
        
        if mode == "Dark":
            style.configure("Treeview",
                            background="#2E2E2E",  # Dark background for the Treeview
                            foreground="white",
                            rowheight=30,  # Row height
                            fieldbackground="#2E2E2E")  # Dark field background

            style.configure("Treeview.Heading",
                            background="#333333",  # Darker header background
                            foreground="white",
                            font=("Helvetica", 12, "bold"),
                            relief="flat")  # Flat relief for modern look

            # Add modern visual effects for headings
            style.map("Treeview.Heading",
                      background=[('active', '#007acc')],  # Change color on hover
                      foreground=[('active', 'white')])

        else:  # Light mode
            style.configure("Treeview",
                            background="#ffffff",  # Light background for the Treeview
                            foreground="#000000",
                            rowheight=30,  # Row height
                            font=("Calibri ", 10),
                            fieldbackground="#ffffff")  # Light field background

            style.configure("Treeview.Heading",
                            background="#edf67d",  # Light grey header background
                            foreground="black",
                            font=("Ubuntu", 12, "bold"),
                            relief="flat")  # Flat relief for modern look

            # Add modern visual effects for headings
            style.map("Treeview.Heading",
                      background=[('active', '#1b263b')],  # Change color on hover
                      foreground=[('active', 'white')])
        
        
    def on_tree_select(self, event):
        selected_item = self.table.selection()
        if selected_item:
            item_values = self.table.item(selected_item, 'values')
            movie_title = item_values[1]
            movie_date = item_values[2] if len (item_values) > 2 else "N\A"
            movie_id = item_values[3]

            self.controller.frames["page2"].update_soup(self.controller.soup, movie_title, movie_date, movie_id)
            self.controller.show_frame("page2")

        

class page2(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.soup = None

        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=1)  
        self.grid_rowconfigure(2, weight=1)  
        self.grid_rowconfigure(3, weight=2)  
        
        self.grid_columnconfigure(0, weight=1)  # First column
        self.grid_columnconfigure(1, weight=1)  # Second column
        self.grid_columnconfigure(2, weight=2)  # Third column (Overview)
        self.grid_columnconfigure(3, weight=2)  # Fourth column (Score)


        self.title_frame = ctk.CTkFrame(self, fg_color=('transparent'), height=100, border_color="#6b9080", border_width=2)
        self.title_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")
        self.title_frame.grid_propagate(False)
        self.title = ctk.CTkLabel(self.title_frame, text="", font=("Arial", 20, 'bold'))
        self.title.pack(pady=30)
        
        button = ctk.CTkButton(self, text="Go Back", command=lambda: controller.show_frame("page1"))
        button.grid(row=0, column=4, padx=10, pady=10, sticky='ew') 

        self.date_frame = ctk.CTkFrame(self, fg_color='#6b9080', height=50, width=50)
        self.date_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.date_frame.grid_propagate(False)
        self.date = ctk.CTkLabel(self.date_frame, text="", font=("Arial", 18), justify='center')
        self.date.pack(fill='both', expand=True)
        self.date.pack_propagate(False)
        
        self.genres_frame = ctk.CTkFrame(self, fg_color='#a4c3b2', height=50, width=50)
        self.genres_frame.grid(row=1, column=1, padx=10, pady=10, columnspan=2, sticky='nsew')
        self.genres_frame.grid_propagate(False)
        self.genres = ctk.CTkLabel(self.genres_frame, text="", font=("Arial", 18), justify='center')
        self.genres.pack(fill='both', expand=True)
        self.genres.pack_propagate(False)
        
        self.runtime_frame = ctk.CTkFrame(self, fg_color='#cce3de', height=50, width=50)
        self.runtime_frame.grid(row=1, column=3, padx=10, pady=10, sticky='nsew')
        self.runtime = ctk.CTkLabel(self.runtime_frame, text="", font=("Arial", 18), justify='center')
        self.runtime_frame.grid_propagate(False)       
        self.runtime.pack(fill='both', expand=True)
        self.runtime.pack_propagate(False)
        
        self.director_frame = ctk.CTkFrame(self, fg_color='#eaf4f4')
        self.director_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.director_frame.grid_propagate(False)
        self.director = ctk.CTkLabel(self.director_frame, text="", font=("Arial", 18), justify='center')
        self.director.pack(fill='both', expand=True)
        self.director.pack_propagate(False)


        self.header_frame = ctk.CTkFrame(self, fg_color='#cce3de')
        self.header_frame.grid(row=2, column=2, columnspan=3, padx=10, pady=10, sticky='nsew')
        self.header_frame.grid_propagate(False)
        self.header = ctk.CTkLabel(self.header_frame, text="", font=("Arial", 18), justify='center')
        self.header.pack(fill='both', expand=True)
        self.header.pack_propagate(False)
        
        self.score_frame = ctk.CTkFrame(self, fg_color='#eaf4f4')
        self.score_frame.grid(row=1, column=4, padx=10, pady=10, sticky='nsew')
        self.score_frame.grid_propagate(False)
        self.score = ctk.CTkLabel(self.score_frame, text="", font=("Arial", 18))
        self.score.pack(fill='both', expand=True)
        
        self.cast_frame = ctk.CTkFrame(self, fg_color='#50808e')
        self.cast_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.cast_frame.grid_propagate(False)
        self.cast = ctk.CTkLabel(self.cast_frame, text="", font=("Arial", 18), justify='left')
        self.cast.pack(fill='both', expand=True)
        
        self.overview_frame = ctk.CTkFrame(self, fg_color='#cce3de')
        self.overview_frame.grid(row=3, column=2, columnspan=3, padx=10, pady=10, sticky='nsew')
        self.overview_frame.grid_propagate(False)
        self.overview = ctk.CTkLabel(self.overview_frame, text="", font=("Arial", 18), wraplength=500, justify='left')
        self.overview.pack(fill='both', expand=True)
        
    def update_soup(self, soup, title, date, movie_id):
        self.title.configure(text=f"{title}")
        
        movie_url = f"https://www.themoviedb.org/movie/{movie_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive'
        }
        new_r = requests.get(movie_url, headers=headers)
        new_soup = BeautifulSoup(new_r.content, 'lxml')
        genres_tag = new_soup.find('span', {'class' : 'genres'})
        genres = genres_tag.get_text(strip=True)
        genres_list = genres.split(',')
        genres_with_space = ', '.join(genre.strip() for genre in genres_list)
        runtime_tag = new_soup.find('span', {'class' : 'runtime'})
        runtime = runtime_tag.get_text(strip=True)
        overview_tag = new_soup.find('div', {'class' : 'overview'})
        overview = overview_tag.get_text(strip=True)
        cast_bigtag = new_soup.find('ol', {'class' : 'people scroller'})
        cast_tag = cast_bigtag.find_all('li', {'class' : 'card'})
        actor_pairs = []
        for actors in cast_tag:
            actor_tag = actors.find('p')
            actor_text = actor_tag.get_text(strip=True)
            characters_tag = actors.find('p', {'class' : 'character'})
            characters = characters_tag.get_text(strip=True)
            actor_pairs.append(f"{actor_text} : {characters}")
        actor_pairs_info = '\n'.join(actor_pairs)
        score = new_soup.find('div', {'class' : 'percent'})
        icon_tags = new_soup.find('span', class_=re.compile(r'icon icon-r\d+'))
        number = None
        if icon_tags:
            class_attr = icon_tags.get('class')
            for cls in class_attr:
                match = re.search(r'r(\d+)', cls)
                if match:
                    number = match.group(1)
                    break
          
        director_tags = new_soup.find('li', {'class' : 'profile'})
        director_tag = director_tags.find('a')
        director = director_tag.get_text(strip=True) if director_tag else "N\A"
        header_info = new_soup.find('h3', {'class' : 'tagline'})
        header_text = header_info.get_text(strip=True) if header_info else "N\A"
        
        self.date.configure(text=f"Date\n {date}")
        self.genres.configure(text=f"Genres\n {genres}")
        self.runtime.configure(text=f"Runtime\n {runtime}")
        self.director.configure(text=f"Director\n {director}")
        self.header.configure(text=f"{header_text}")
        self.score.configure(text=f"Score\n {number}")
        self.cast.configure(text=f"{actor_pairs_info}")
        self.overview.configure(text=f"{overview}")


        
if __name__ == "__main__":
    app = App()
    app.mainloop()