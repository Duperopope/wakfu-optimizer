/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aKZ
implements aqz {
    protected int o;
    protected int asJ;
    protected int Nf;
    protected int[] egC;

    public int d() {
        return this.o;
    }

    public int aGD() {
        return this.asJ;
    }

    public int apw() {
        return this.Nf;
    }

    public int[] cjO() {
        return this.egC;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.asJ = 0;
        this.Nf = 0;
        this.egC = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.asJ = aqH2.bGI();
        this.Nf = aqH2.bGI();
        this.egC = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.oAj.d();
    }
}
