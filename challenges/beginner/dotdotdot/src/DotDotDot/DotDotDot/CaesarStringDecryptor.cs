using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DotDotDot
{
    public class CaesarStringDecryptor : IStringDecryptor
    {
        private readonly int _offset;

        public CaesarStringDecryptor(int offset)
        {
            _offset = offset;
        }
        public string DecryptString(string input)
        {
            string output = string.Empty;

            foreach (var c in input)
            {
                if (c >= 'A' && c <= 'Z')
                {
                    int alphabetOffset = c - 'A' - _offset;
                    alphabetOffset += 26;
                    alphabetOffset %= 26;
                    output += (char)('A' + alphabetOffset);
                }
                else if (c >= 'a' && c <= 'z')
                {
                    int alphabetOffset = c - 'a' - _offset;
                    alphabetOffset += 26;
                    alphabetOffset %= 26;
                    output += (char)('a' + alphabetOffset);
                }
                else
                {
                    output += c;
                }
            }

            return output;
        }
    }
}
