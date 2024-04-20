from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox, QToolBar, QStatusBar, \
    QMessageBox
import sys
import sqlite3

class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800,600)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon("icons/icons/add.png"),"Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.About)

        search_action = QAction(QIcon("icons/icons/search.png"),"search", self)
        search_action.triggered.connect(self.Search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)


    def cell_clicked(self):
        edit_btn = QPushButton("Edit Record")
        edit_btn.clicked.connect(self.edit)

        delete_btn = QPushButton("Delete Record")
        delete_btn.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_btn)
        self.statusbar.addWidget(delete_btn)



    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)

        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def Search(self):
        search = search_Dialog()
        search.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def About(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created with python and sqlite3.
        It is a Student Management App
        Feel free to modify and reuse this app
        """
        self.setText(content)



class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation_message = QLabel("Are you sure you want to delete this Record ?")
        self.yes = QPushButton("Yes")
        self.no = QPushButton("No")

        layout.addWidget(confirmation_message, 0, 0, 1, 2)
        layout.addWidget(self.yes, 1, 0)
        layout.addWidget(self.no, 1, 1)
        self.setLayout(layout)

        self.yes.clicked.connect(self.delete_student)


    def delete_student(self):
        # Get index and Student id from selected row
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()


        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully! ")
        confirmation_widget.exec()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()

        # Get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # Add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        course_name = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Add phone number
        phone_number = main_window.table.item(index, 3).text()
        self.phone_number = QLineEdit(phone_number)
        self.phone_number.setPlaceholderText("Mobile")
        layout.addWidget(self.phone_number)

        # submit button
        self.button = QPushButton("Update")
        self.button.clicked.connect(self.update)
        layout.addWidget(self.button)

        self.setLayout(layout)


    def update(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                                    self.course_name.itemText(self.course_name.currentIndex()),
                                    self.phone_number.text(),
                                    self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh the table
        main_window.load_data()




class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)


        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add phone number
        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("Mobile")
        layout.addWidget(self.phone_number)

        # submit button
        self.button = QPushButton("Register")
        self.button.clicked.connect(self.add_student)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.phone_number.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students(name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class search_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Window")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.name = QLineEdit()
        self.name.setPlaceholderText("Name")
        layout.addWidget(self.name)

        self.btn = QPushButton("Search")
        layout.addWidget(self.btn)
        self.btn.clicked.connect(self.search)


        self.setLayout(layout)

    def search(self):
        name = self.name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        main_window.table.setRowCount(len(rows))  # Update table row count
        for row_number, row_data in enumerate(rows):
            for column_number, data in enumerate(row_data):
                main_window.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        cursor.close()
        connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())