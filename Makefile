# Set the compiler
CXX = g++

# Define the directories where the headers and libraries are located
INCLUDE_PATH = /opt/homebrew/include
LIBRARY_PATH = /opt/homebrew/lib

# Define source and build directories
SRC_DIR = src
BUILD_DIR = build

# Compiler flags
CXXFLAGS = -I$(INCLUDE_PATH) -std=c++11

# Linker flags
LDFLAGS = -L$(LIBRARY_PATH) -lglew -lglfw -framework OpenGL

# Name of the output program
TARGET = $(BUILD_DIR)/my_program

# Source files
SRC = $(SRC_DIR)/main.cpp

# Object files
OBJ = $(BUILD_DIR)/main.o  # Object file will go in the build directory

# Default target to build the program
all: $(TARGET)

# Rule to compile the program
$(TARGET): $(OBJ)
	$(CXX) $(OBJ) -o $(TARGET) $(LDFLAGS)

# Rule to compile the .cpp file to a .o file
$(BUILD_DIR)/main.o: $(SRC_DIR)/main.cpp
	$(CXX) $(CXXFLAGS) -c $(SRC_DIR)/main.cpp -o $(BUILD_DIR)/main.o

# Clean up build files
clean:
	rm -f $(OBJ) $(TARGET)
