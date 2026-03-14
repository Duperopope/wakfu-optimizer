/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fuC
implements aqz {
    protected int o;
    protected int[] egL;
    protected int[] tyB;

    public int d() {
        return this.o;
    }

    public int[] cjX() {
        return this.egL;
    }

    public int[] gnu() {
        return this.tyB;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.egL = null;
        this.tyB = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.egL = aqH2.bGM();
        this.tyB = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.oAa.d();
    }
}
