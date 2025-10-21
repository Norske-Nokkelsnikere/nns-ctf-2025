using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DotDotDot
{
    internal class CaesarStringDecryptorBuilder
    {
        internal int _offset;

        internal CaesarStringDecryptorBuilder SetOffset(int offset)
        {
            _offset = offset;
            return this;
        }

        internal CaesarStringDecryptor Build()
        {
            return new(_offset);
        }
    }
}
