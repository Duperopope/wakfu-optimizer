/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fwi
implements aqz {
    protected int o;
    protected int elz;
    protected short elA;
    protected int asA;
    protected short bol;

    public int d() {
        return this.o;
    }

    public int coR() {
        return this.elz;
    }

    public short coS() {
        return this.elA;
    }

    public int azv() {
        return this.asA;
    }

    public short bfd() {
        return this.bol;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.elz = 0;
        this.elA = 0;
        this.asA = 0;
        this.bol = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.elz = aqH2.bGI();
        this.elA = aqH2.bGG();
        this.asA = aqH2.bGI();
        this.bol = aqH2.bGG();
    }

    @Override
    public final int bGA() {
        return ewj.oBf.d();
    }
}
