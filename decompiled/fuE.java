/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fuE
implements aqz {
    protected int o;
    protected int[] tyC;
    protected int[] tyB;
    protected short tyD;
    protected String egv;
    protected short tyE;
    protected String tyF;

    public int d() {
        return this.o;
    }

    public int[] gnv() {
        return this.tyC;
    }

    public int[] gnu() {
        return this.tyB;
    }

    public short gnw() {
        return this.tyD;
    }

    public String cjH() {
        return this.egv;
    }

    public short gnx() {
        return this.tyE;
    }

    public String gny() {
        return this.tyF;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.tyC = null;
        this.tyB = null;
        this.tyD = 0;
        this.egv = null;
        this.tyE = 0;
        this.tyF = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.tyC = aqH2.bGM();
        this.tyB = aqH2.bGM();
        this.tyD = aqH2.bGG();
        this.egv = aqH2.bGL().intern();
        this.tyE = aqH2.bGG();
        this.tyF = aqH2.bGL().intern();
    }

    @Override
    public final int bGA() {
        return ewj.ozZ.d();
    }
}
