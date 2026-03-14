/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  aOr
 *  aqz
 */
import java.util.HashMap;

public class aOq
implements aqz {
    protected int o;
    protected int bIi;
    protected int eqU;
    protected short eqV;
    protected short eqW;
    protected boolean eqX;
    protected boolean eqY;
    protected boolean eqZ;
    protected boolean era;
    protected short erb;
    protected int[] baD;
    protected int[] erc;
    protected aOr[] erd;
    protected short aAw;
    protected int ere;
    protected HashMap<Long, int[]> erf;

    public int d() {
        return this.o;
    }

    public int aeV() {
        return this.bIi;
    }

    public int cuw() {
        return this.eqU;
    }

    public short cux() {
        return this.eqV;
    }

    public short cuy() {
        return this.eqW;
    }

    public boolean cuz() {
        return this.eqX;
    }

    public boolean cuA() {
        return this.eqY;
    }

    public boolean cuB() {
        return this.eqZ;
    }

    public boolean cuC() {
        return this.era;
    }

    public short cuD() {
        return this.erb;
    }

    public int[] ckm() {
        return this.baD;
    }

    public int[] cuE() {
        return this.erc;
    }

    public aOr[] cuF() {
        return this.erd;
    }

    public short aKu() {
        return this.aAw;
    }

    public int cuG() {
        return this.ere;
    }

    public HashMap<Long, int[]> cuH() {
        return this.erf;
    }

    public void reset() {
        this.o = 0;
        this.bIi = 0;
        this.eqU = 0;
        this.eqV = 0;
        this.eqW = 0;
        this.eqX = false;
        this.eqY = false;
        this.eqZ = false;
        this.era = false;
        this.erb = 0;
        this.baD = null;
        this.erc = null;
        this.erd = null;
        this.aAw = 0;
        this.ere = 0;
        this.erf = null;
    }

    public void a(aqH aqH2) {
        int n;
        this.o = aqH2.bGI();
        this.bIi = aqH2.bGI();
        this.eqU = aqH2.bGI();
        this.eqV = aqH2.bGG();
        this.eqW = aqH2.bGG();
        this.eqX = aqH2.bxv();
        this.eqY = aqH2.bxv();
        this.eqZ = aqH2.bxv();
        this.era = aqH2.bxv();
        this.erb = aqH2.bGG();
        this.baD = aqH2.bGM();
        this.erc = aqH2.bGM();
        int n2 = aqH2.bGI();
        this.erd = new aOr[n2];
        for (n = 0; n < n2; ++n) {
            this.erd[n] = new aOr();
            this.erd[n].a(aqH2);
        }
        this.aAw = aqH2.bGG();
        this.ere = aqH2.bGI();
        n = aqH2.bGI();
        this.erf = new HashMap(n);
        for (int i = 0; i < n; ++i) {
            long l = aqH2.bGK();
            int[] nArray = aqH2.bGM();
            this.erf.put(l, nArray);
        }
    }

    public final int bGA() {
        return ewj.ozy.d();
    }
}
