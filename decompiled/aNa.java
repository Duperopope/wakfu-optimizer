/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aNa
implements aqz {
    protected short avX;
    protected short emz;
    protected boolean emA;
    protected boolean emB;
    protected String[] emC;
    protected String[] emD;
    protected boolean emE;
    protected short emF;

    public short aIi() {
        return this.avX;
    }

    public short cpX() {
        return this.emz;
    }

    public boolean cpY() {
        return this.emA;
    }

    public boolean cpZ() {
        return this.emB;
    }

    public String[] cqa() {
        return this.emC;
    }

    public String[] cqb() {
        return this.emD;
    }

    public boolean cqc() {
        return this.emE;
    }

    public short cqd() {
        return this.emF;
    }

    @Override
    public void reset() {
        this.avX = 0;
        this.emz = 0;
        this.emA = false;
        this.emB = false;
        this.emC = null;
        this.emD = null;
        this.emE = false;
        this.emF = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.avX = aqH2.bGG();
        this.emz = aqH2.bGG();
        this.emA = aqH2.bxv();
        this.emB = aqH2.bxv();
        this.emC = aqH2.bGO();
        this.emD = aqH2.bGO();
        this.emE = aqH2.bxv();
        this.emF = aqH2.bGG();
    }

    @Override
    public final int bGA() {
        return ewj.ozb.d();
    }
}
