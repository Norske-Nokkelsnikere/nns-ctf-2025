using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DotDotDot
{
    public class XorStringDecryptor : IStringDecryptor
    {
        private byte[] _key;

        public XorStringDecryptor(byte[] key)
        {
            _key = key;
        }

        public string DecryptString(string input)
        {
            string output = string.Empty;
            for (int i = 0; i < input.Length; i++)
            {
                output += (char)(input[i] ^ _key[i % _key.Length]);
            }

            return output;
        }
    }
}
