#include "api.hpp"
#include <iostream>
#include <fstream>
#include <string>

extern DFA dfa_minim(DFA &d);

int main() {
  std::ifstream infile("../dfa_minim.in");
  std::ofstream outfile("../dfa_minim.out");
  auto d = DFA::from_string(std::string((std::istreambuf_iterator<char>(infile)), 
                                   std::istreambuf_iterator<char>()));
  outfile << dfa_minim(d).to_string();
  return 0;
}
