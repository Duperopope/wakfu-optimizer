/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aOT
implements aqz {
    protected int o;
    protected double ejs;
    protected short enb;
    protected short enc;
    protected String eik;
    protected short euL;
    protected short[] euM;
    protected short[] euN;
    protected aOU[] euO;

    public int d() {
        return this.o;
    }

    public double cmK() {
        return this.ejs;
    }

    public short cqz() {
        return this.enb;
    }

    public short cqA() {
        return this.enc;
    }

    public String clB() {
        return this.eik;
    }

    public short cyv() {
        return this.euL;
    }

    public short[] cyw() {
        return this.euM;
    }

    public short[] cyx() {
        return this.euN;
    }

    public aOU[] cyy() {
        return this.euO;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ejs = 0.0;
        this.enb = 0;
        this.enc = 0;
        this.eik = null;
        this.euL = 0;
        this.euM = null;
        this.euN = null;
        this.euO = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ejs = aqH2.bGJ();
        this.enb = aqH2.bGG();
        this.enc = aqH2.bGG();
        this.eik = aqH2.bGL().intern();
        this.euL = aqH2.bGG();
        this.euM = aqH2.bGN();
        this.euN = aqH2.bGN();
        int n = aqH2.bGI();
        this.euO = new aOU[n];
        for (int i = 0; i < n; ++i) {
            this.euO[i] = new aOU();
            ((aOu)this.euO[i]).a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.ozM.d();
    }
}
