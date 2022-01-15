#include "Student.h"

std::ostream& operator<<(std::ostream& os, const Student& student) {
	return os << student.getName() << " "
		<< student.getAge() << " "
		<< student.getStudyLevel();
}