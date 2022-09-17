#include "api.hpp"
#include <iostream>
#include <fstream>
#include <string>

extern std::string dfa2re(DFA &d);

int main() {
  std::ifstream infile("dfa2re.in");
  std::ofstream outfile("dfa2re.out");
  auto d = DFA::from_string(std::string((std::istreambuf_iterator<char>(infile)), 
                                   std::istreambuf_iterator<char>()));
  outfile << dfa2re(d);
  return 0;
}
