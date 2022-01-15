#include <iostream>
#include "Faculty.h"

void keep_window() {
	char c;
	std::cin>>c;
}

int main() {
	
	Student student1("Denis", 22, 2);
	Student student2("Elma", 19, 1);
	Student student3("Tarik", 24, 2);
	Student student4("Adin", 19, 1);
	Student student5("Zlatan", 26, 3);

	Professor professor1("Prof1", 37);
	Professor professor2("Prof2", 41);
	Professor professor3("Prof3", 54);

	Faculty faculty("Polytechnic faculty");

	faculty.addStudent(student1);
	faculty.addStudent(student2);
	faculty.addStudent(student3);
	faculty.addStudent(student4);
	faculty.addStudent(student5);

	professor1.addTeachingSubject("Calculus 1", 30, 40);
	professor1.addTeachingSubject("Calculus 2", 25, 35);
	professor1.addTeachingSubject("Computer networks", 35, 37);

	professor2.addTeachingSubject("Algorithms & data structures", 30, 40);
	professor2.addTeachingSubject("Introduction to databases", 25, 35);
	professor2.addTeachingSubject("Introduction to programming", 35, 37);

	professor3.addTeachingSubject("Cybersecurity", 30, 40);
	professor3.addTeachingSubject("Information security", 25, 35);

	faculty.addProfessor(professor1);
	faculty.addProfessor(professor2);
	faculty.addProfessor(professor3);

	std::cout << std::endl;
	std::cout << "Students at " << faculty.getName() << ":" << std::endl;
	std::cout << "-----" << std::endl;

	for (const Student& student : faculty.getStudents()) {
		std::cout << student << std::endl;
	}

	std::cout << std::endl;

	std::cout << "Professors at " << faculty.getName() << ":" << std::endl;
	std::cout << "-----" << std::endl;

	for (const Professor& professor : faculty.getProfessors()) {
		std::cout << professor << std::endl;
	}

	keep_window();
	return 0;
}