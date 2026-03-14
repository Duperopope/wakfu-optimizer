/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 *  fkj
 */
public class aLF
implements aqz {
    protected int o;
    protected int eiF;
    protected int eiG;
    protected String eiH;
    protected String eiI;
    protected int[] eiJ;

    public int d() {
        return this.o;
    }

    public int clW() {
        return this.eiF;
    }

    public int clX() {
        return this.eiG;
    }

    public String clY() {
        return this.eiH;
    }

    public String ajo() {
        return this.eiI;
    }

    public int[] clZ() {
        return this.eiJ;
    }

    public fkj[] cma() {
        fkj[] fkjArray = new fkj[this.eiJ.length];
        for (int i = 0; i < this.eiJ.length; ++i) {
            fkjArray[i] = fkj.WL((int)this.eiJ[i]);
        }
        return fkjArray;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.eiF = 0;
        this.eiG = 0;
        this.eiH = null;
        this.eiI = null;
        this.eiJ = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.eiF = aqH2.bGI();
        this.eiG = aqH2.bGI();
        this.eiH = aqH2.bGL().intern();
        this.eiI = aqH2.bGL().intern();
        this.eiJ = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.oyH.d();
    }
}
