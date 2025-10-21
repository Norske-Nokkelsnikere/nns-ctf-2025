using DotDotDot;

Console.WriteLine(" ____        _   ____        _   ____        _         \r\n|  _ \\  ___ | |_|  _ \\  ___ | |_|  _ \\  ___ | |_       \r\n| | | |/ _ \\| __| | | |/ _ \\| __| | | |/ _ \\| __|      \r\n| |_| | (_) | |_| |_| | (_) | |_| |_| | (_) | |_ _ _ _ \r\n|____/ \\___/ \\__|____/ \\___/ \\__|____/ \\___/ \\__(_|_|_)\n");

string encoded_flag = "\x11\x2a\x38\x1e\x55\x64\x0a\x0b\x54\x47\x7f\x54\x03\x31\x56\x53\x0b\x5c\x0e\x11\x33\x55\x1b\x15\x5e\x0a\x49\x11\x2b\x56\x1c\x33\x0e\x10\x3d\x13\x55\x02\x49\x1f\x59\x3a\x1a\x5e\x10\x56\x15";
string tore_tang = "Tore Tang, ein gammal mann. Heile byen kjenne han, Han som leve av gammalt brod og vann. Kor han komme fra vett bare han, Tore Tang.";
int offset = 17;

var xor_builder = new XorStringDecryptorBuilder();
var xor_decryptor = xor_builder
    .SetKey(tore_tang.Select(x => (byte)x).ToArray())
    .Build();

var caesar_builder = new CaesarStringDecryptorBuilder();
var caesar_decryptor = caesar_builder
    .SetOffset(offset)
    .Build();

var caesar_flag = xor_decryptor.DecryptString(encoded_flag);

var decrypted_flag = caesar_decryptor.DecryptString(caesar_flag);

Console.WriteLine("Enter the flag to check if it is right.");

while (true)
{
    Console.Write("> ");

    var input_flag = Console.ReadLine();

    if (input_flag == decrypted_flag)
    {
        Console.WriteLine("Correct, well done!");
        break;
    }
    else
    {
        Console.WriteLine("Nope. Try again\n");
    }
}