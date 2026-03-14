/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  BH
 *  aqJ
 */
import java.nio.ByteBuffer;

public class aqH
extends aqJ {
    private final ByteBuffer cQX;

    public aqH(ByteBuffer byteBuffer, int n, int n2) {
        super(n, n2);
        this.cQX = byteBuffer;
    }

    public long bGF() {
        return this.cQX.position();
    }

    protected void a(int n, byte by) {
        this.cRa = by;
        this.cQX.position(n);
    }

    public byte aTf() {
        this.bGQ();
        return (byte)(this.cQX.get() - this.cRa);
    }

    public boolean bxv() {
        this.bGQ();
        return this.cQX.get() - this.cRa != 0;
    }

    public short bGG() {
        this.bGQ();
        return (short)(this.cQX.getShort() - this.cRa);
    }

    public float bGH() {
        this.bGQ();
        return this.cQX.getFloat();
    }

    public int bGI() {
        this.bGQ();
        return this.cQX.getInt() - this.cRa;
    }

    public double bGJ() {
        this.bGQ();
        return this.cQX.getDouble();
    }

    public long bGK() {
        this.bGQ();
        return this.cQX.getLong() - (long)this.cRa;
    }

    public String bGL() {
        int n = this.bGI();
        byte[] byArray = new byte[n];
        this.cQX.get(byArray);
        return BH.dc((byte[])byArray);
    }

    public byte[] bxB() {
        int n = this.bGI();
        byte[] byArray = new byte[n];
        for (int i = 0; i < n; ++i) {
            byArray[i] = this.aTf();
        }
        return byArray;
    }

    public int[] bGM() {
        int n = this.bGI();
        int[] nArray = new int[n];
        for (int i = 0; i < n; ++i) {
            nArray[i] = this.bGI();
        }
        return nArray;
    }

    public short[] bGN() {
        int n = this.bGI();
        short[] sArray = new short[n];
        for (int i = 0; i < n; ++i) {
            sArray[i] = this.bGG();
        }
        return sArray;
    }

    public float[] bxA() {
        int n = this.bGI();
        float[] fArray = new float[n];
        for (int i = 0; i < n; ++i) {
            fArray[i] = this.bGH();
        }
        return fArray;
    }

    public String[] bGO() {
        int n = this.bGI();
        String[] stringArray = new String[n];
        for (int i = 0; i < n; ++i) {
            stringArray[i] = this.bGL();
        }
        return stringArray;
    }

    public long[] bxz() {
        int n = this.bGI();
        long[] lArray = new long[n];
        for (int i = 0; i < n; ++i) {
            lArray[i] = this.bGK();
        }
        return lArray;
    }
}
