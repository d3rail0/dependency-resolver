#include "Professor.h"

std::ostream& operator<<(std::ostream& os, const Professor& professor) {
	
	os  << professor.getName() << " "
		<< professor.getAge() << " "
		<< "Teaching subjecs = [";

	std::vector<Subject> teSubs = professor.getTeachingSubjects();
	for (size_t i = 0; i < teSubs.size(); i++) {
		os << teSubs[i].name;
		if (i == teSubs.size() - 1)
			break;
		os << ", ";
	}

	return os << "]";
}