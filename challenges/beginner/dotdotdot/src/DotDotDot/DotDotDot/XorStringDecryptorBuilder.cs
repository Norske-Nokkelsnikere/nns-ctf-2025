using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DotDotDot
{
    public class XorStringDecryptorBuilder
    {
        internal byte[] _key = [];

        internal XorStringDecryptorBuilder SetKey(byte[] key)
        {
            _key = key;
            return this;
        }

        internal XorStringDecryptor Build()
        {
            return new(_key);
        }
    }
}
