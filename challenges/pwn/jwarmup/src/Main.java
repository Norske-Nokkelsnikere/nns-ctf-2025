import sun.misc.Unsafe;

import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        var flag = System.getenv("FLAG");
        if (flag == null) {
            flag = "NNS{fake_flag}";
        }

        var safe = getSafe();

        Object[] arr = new Object[]{flag};
        var string = Long.toHexString(safe.getLong(arr, 16));
        System.out.println("Here you go: " + string);

        var scanner = new Scanner(System.in);
        while (true) {
            try {
                System.out.print("Enter an address to read: ");
                var address = Long.valueOf(scanner.nextLine(), 16);
                var out = safe.getByte(address);
                System.out.printf("You read: %02X\n", out);
            } catch (NumberFormatException ignored) {
                System.err.println("Bad");
                System.exit(1);
            }
        }
    }

    private static Unsafe getSafe() {
        try {
            var f = Unsafe.class.getDeclaredField("theUnsafe");
            f.setAccessible(true);
            return (Unsafe) f.get(null);
        } catch (Exception e) {
            throw new IllegalStateException("Boring", e);
        }
    }
}
